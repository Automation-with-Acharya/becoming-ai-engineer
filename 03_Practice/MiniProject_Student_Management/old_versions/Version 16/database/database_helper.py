"""
Database Helper Module.

This module manages PostgreSQL database connections and SQL query executions using psycopg library.

Day 017 Update: All print() statements replaced with structured logger calls.
                Exception logging via logger.exception() inside try/except blocks to capture full stack traces.
Day 019 Update: Database connection settings now read from config.py / .env (Exercise 5).
                Removed individual os.getenv() calls — settings object is the single source of truth.
Day 020 Update: Proper ACID transaction handling added.
                execute_write() wraps single write queries in an explicit BEGIN/COMMIT/ROLLBACK block.
                execute_write_transaction() runs a caller-supplied sequence of queries atomically.
                execute_query() now issues a rollback on failure to leave the connection in a clean state.
Day 021 Update: Single persistent connection replaced with psycopg_pool.ConnectionPool (Exercise 3).
                Each query borrows a connection from the pool for exactly one operation and returns it
                immediately — the pool is shared across all concurrent requests.
                open_pool() / close_pool() manage the pool lifecycle and are called from main.py lifespan.
Day 022 Update: Database indexes added for performance.
                - idx_students_email : UNIQUE B-Tree index on email — enforces uniqueness and makes
                  exact-match lookups (WHERE email = ...) O(log N) instead of O(N) full-table scans.
                - idx_students_name  : B-Tree index on name — accelerates prefix searches
                  (WHERE name ILIKE 'alice%') and exact equality lookups on large datasets.
                Both indexes are created with IF NOT EXISTS so startup remains idempotent.
"""

import psycopg
from psycopg_pool import ConnectionPool

from config import settings
from logger_config import get_logger

logger = get_logger(__name__)


class DatabaseHelper:
    """
    A helper class to manage PostgreSQL database connections via a connection pool.

    Day 021: Replaced the single self.connection with a psycopg_pool.ConnectionPool.

    Why a pool instead of a single connection?
    ------------------------------------------
    A single persistent connection is a bottleneck: only one query can run at a time, and
    if that connection drops the whole app loses DB access until restart.

    A connection pool keeps a configurable number of ready-to-use connections:
    - Each incoming request checks out a connection, uses it, and returns it immediately.
    - Multiple concurrent requests can each have their own connection (up to max_size).
    - If all connections are in use, new requests wait in a queue (bounded by a timeout).
    - If a connection goes stale/dead, the pool replaces it automatically.

    Pool lifecycle (managed by FastAPI lifespan in main.py):
        Startup  → open_pool()   opens min_size connections to PostgreSQL
        Runtime  → with self._pool.connection() as conn: ...   (borrow / return)
        Shutdown → close_pool()  cleanly closes all pool connections
    """

    def __init__(self, dbname=None, user=None, password=None, host=None, port=None):
        """
        Store connection parameters. The pool itself is not created here;
        call open_pool() during application startup (lifespan).

        If arguments are passed explicitly (e.g., from tests), they take priority.
        Otherwise values are read from the centralized settings object which
        sources from .env / environment variables (Day 019 Exercise 5).

        Args:
            dbname   (str, optional): PostgreSQL database name.
            user     (str, optional): PostgreSQL username.
            password (str, optional): PostgreSQL password.
            host     (str, optional): Database server host.
            port     (str, optional): Database server port.
        """
        # Day 019 Exercise 5: Prefer explicit args (useful in tests), fall back to settings.
        self.dbname   = dbname   or settings.db_name
        self.user     = user     or settings.db_user
        self.host     = host     or settings.db_host
        self.port     = port     or str(settings.db_port)

        _raw_password = password if password is not None else settings.db_password
        # settings.db_password is declared as SecretStr in config.py — unwrap it.
        self.password = (
            _raw_password.get_secret_value()
            if hasattr(_raw_password, "get_secret_value")
            else _raw_password
        )

        # Day 021: Pool object — None until open_pool() is called.
        self._pool: ConnectionPool | None = None

        logger.debug(
            "DatabaseHelper initialized — host=%s, port=%s, db=%s, user=%s",
            self.host, self.port, self.dbname, self.user,
        )

    # ──────────────────────────────────────────────────────────────────────────
    # Day 021 Exercise 3 & 4: Pool lifecycle — called from FastAPI lifespan
    # ──────────────────────────────────────────────────────────────────────────

    @property
    def conninfo(self) -> str:
        """Build a psycopg conninfo string from the stored credentials."""
        return (
            f"host={self.host} port={self.port} dbname={self.dbname} "
            f"user={self.user} password={self.password}"
        )

    def open_pool(self) -> None:
        """
        Day 021 Exercise 3: Open the connection pool.

        Called once during FastAPI lifespan STARTUP. Creates min_size connections
        immediately so the first requests do not incur connection overhead.

        Also runs _create_table_if_not_exists() to ensure the schema is ready
        before the app starts accepting traffic (same guarantee as the old connect()).
        """
        if self._pool is not None:
            logger.warning("open_pool() called but pool is already open — skipping.")
            return

        min_size = settings.db_pool_min_size
        max_size = settings.db_pool_max_size

        logger.info(
            "[Pool] Opening connection pool — host=%s db=%s min=%d max=%d",
            self.host, self.dbname, min_size, max_size,
        )
        try:
            self._pool = ConnectionPool(
                conninfo=self.conninfo,
                min_size=min_size,
                max_size=max_size,
                open=True,          # Open connections immediately (not lazily)
            )
            # Verify schema on startup (same responsibility as the old _create_table_if_not_exists)
            self._create_table_if_not_exists()
            logger.info("[Pool] Connection pool opened and schema verified.")
        except Exception:
            logger.exception("[Pool] Failed to open connection pool.")
            raise

    def close_pool(self) -> None:
        """
        Day 021 Exercise 3: Close the connection pool.

        Called once during FastAPI lifespan SHUTDOWN. Waits for all checked-out
        connections to be returned, then closes them all cleanly.
        """
        if self._pool is None:
            logger.warning("close_pool() called but pool is already closed — skipping.")
            return
        try:
            self._pool.close()
            self._pool = None
            logger.info("[Pool] Connection pool closed successfully.")
        except Exception:
            logger.exception("[Pool] Error occurred while closing the connection pool.")

    def _create_table_if_not_exists(self) -> None:
        """
        Create the 'students' table if it does not already exist in PostgreSQL.
        Includes all columns: id, name, age, city, email.

        Day 022: After creating the table, two B-Tree indexes are also created (idempotently):

          1. idx_students_email  (UNIQUE)
             WHY: email is the natural unique identifier for a student account — used in
             authentication flows, duplicate-prevention checks, and direct profile lookups.
             A UNIQUE B-Tree index on email achieves two goals at once:
               a) Enforces the data-integrity constraint (no two students share an email).
               b) Turns every WHERE email = %s query from a sequential full-table scan
                  O(N) into a B-Tree point lookup O(log N).
             At 10,000 students a full scan reads ~10,000 rows; the index reads ~14 (log₂ 10000).

          2. idx_students_name  (non-unique)
             WHY: name is the column targeted by search_students() via ILIKE patterns.
             A plain B-Tree index accelerates prefix searches (ILIKE 'Alice%') because
             PostgreSQL can use an index range scan for leading-wildcard-free patterns.
             For full wildcard patterns (ILIKE '%alice%'), the index does not help and
             PostgreSQL falls back to a seq-scan — upgrading to pg_trgm + GIN index
             would fully solve that case, but is left as a future improvement.

        Both indexes use IF NOT EXISTS so this method is safe to call on every startup.

        Uses a borrowed pool connection so it follows the same borrow/return pattern
        as all other operations.
        """
        logger.debug("Checking/creating 'students' table schema and indexes...")
        with self._pool.connection() as conn:
            with conn.cursor() as cur:
                # ── Table ──────────────────────────────────────────────────────────
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS students (
                        id    INTEGER      PRIMARY KEY,
                        name  VARCHAR(100) NOT NULL,
                        age   INTEGER,
                        city  VARCHAR(100),
                        email VARCHAR(100) UNIQUE
                    )
                    """
                )

                # ── Index 1: UNIQUE B-Tree on email ────────────────────────────────
                # Exact-match lookups (WHERE email = %s) become O(log N).
                # The UNIQUE constraint also prevents duplicate email registrations.
                cur.execute(
                    """
                    CREATE UNIQUE INDEX IF NOT EXISTS idx_students_email
                        ON students (email)
                    """
                )

                # ── Index 2: B-Tree on name ────────────────────────────────────────
                # Accelerates prefix ILIKE patterns (e.g. ILIKE 'Alice%') used in
                # search_students(). Full-wildcard patterns ('%alice%') still seq-scan.
                cur.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_students_name
                        ON students (name)
                    """
                )

            conn.commit()
        logger.debug("'students' table and indexes are ready.")

    # ──────────────────────────────────────────────────────────────────────────
    # Internal helper — ensures pool is open before any query
    # ──────────────────────────────────────────────────────────────────────────

    def _assert_pool_open(self) -> None:
        """Raise RuntimeError if open_pool() has not been called yet."""
        if self._pool is None:
            raise RuntimeError(
                "DatabaseHelper: pool is not open. "
                "Call open_pool() during application startup (lifespan)."
            )

    # ──────────────────────────────────────────────────────────────────────────
    # Query API — same surface as before; pool replaces self.connection
    # ──────────────────────────────────────────────────────────────────────────

    def execute_query(self, query: str, params=None, commit: bool = False):
        """
        Execute an SQL query (SELECT or write-with-commit) against the pool.

        Prefer execute_write() for INSERT / UPDATE / DELETE — it wraps the
        operation in an explicit transaction with automatic rollback on failure.
        Use this method for SELECT queries (commit=False).

        Day 021: Borrows one connection from the pool for the duration of this
        call and returns it automatically when the `with` block exits.

        Args:
            query  (str):            SQL query statement.
            params (tuple, optional): Query parameters.
            commit (bool):           Whether to commit after executing.

        Returns:
            list | None: Query results if rows exist, otherwise None.

        Raises:
            Exception: Re-raises any psycopg database error after logging and rollback.
        """
        self._assert_pool_open()
        try:
            with self._pool.connection() as conn:      # borrow from pool
                with conn.cursor() as cur:
                    cur.execute(query, params)
                    result = cur.fetchall() if cur.description else None
                if commit:
                    conn.commit()
            logger.debug("Query executed successfully: %.80s", query.strip())
            return result
        except Exception:
            # Day 020: Log + rollback. With the pool pattern, rollback is handled
            # automatically by psycopg_pool when the connection context exits on exception.
            logger.exception("Database query failed. Query: %.80s", query.strip())
            raise

    def execute_write(self, query: str, params=None) -> None:
        """
        Day 020 / Day 021: Execute a single write (INSERT / UPDATE / DELETE) inside an
        explicit ACID transaction, using a pooled connection.

        Borrows one connection, opens an explicit transaction via connection.transaction(),
        executes the write, then returns the connection to the pool.

        ACID properties guaranteed:
          - Atomicity   : write fully succeeds or is rolled back automatically.
          - Consistency : DB constraints checked before COMMIT.
          - Isolation   : READ COMMITTED (PostgreSQL default).
          - Durability  : committed data survives server restarts.

        Args:
            query  (str):            SQL INSERT / UPDATE / DELETE statement.
            params (tuple, optional): Query parameters.

        Raises:
            Exception: Re-raises any database error after rollback and logging.
        """
        self._assert_pool_open()
        try:
            with self._pool.connection() as conn:       # borrow from pool
                with conn.transaction():                # BEGIN … COMMIT / ROLLBACK
                    with conn.cursor() as cur:
                        cur.execute(query, params)
            logger.debug("Write transaction committed: %.80s", query.strip())
        except Exception:
            logger.exception("Write transaction rolled back. Query: %.80s", query.strip())
            raise

    def execute_write_transaction(self, steps) -> object:
        """
        Day 020 / Day 021: Execute multiple write queries as a single atomic transaction,
        using a pooled connection.

        Borrows one connection, opens a transaction, then calls steps(cursor).
        All SQL inside steps() shares the same cursor and the same transaction.
        Returns whatever steps() returns (e.g., a newly assigned ID).

        Args:
            steps (callable): Function accepting a psycopg cursor; return value forwarded.

        Returns:
            Any: Whatever steps(cursor) returns.

        Raises:
            Exception: Re-raises any database error after rollback and logging.
        """
        self._assert_pool_open()
        try:
            with self._pool.connection() as conn:       # borrow from pool
                with conn.transaction():                # BEGIN … COMMIT / ROLLBACK
                    with conn.cursor() as cur:
                        result = steps(cur)
            logger.debug("Multi-step write transaction committed.")
            return result
        except Exception:
            logger.exception("Multi-step write transaction rolled back.")
            raise

    def fetch_all(self, query: str, params=None) -> list:
        """
        Fetch all matching rows for a SELECT query.

        Args:
            query  (str):            SQL SELECT query statement.
            params (tuple, optional): Query parameters.

        Returns:
            list: List of row tuples matching query (empty list if none).
        """
        return self.execute_query(query, params=params, commit=False) or []

    def fetch_one(self, query: str, params=None):
        """
        Fetch a single matching row for a SELECT query.

        Args:
            query  (str):            SQL SELECT query statement.
            params (tuple, optional): Query parameters.

        Returns:
            tuple | None: First matching row tuple, or None if no record found.
        """
        rows = self.fetch_all(query, params)
        return rows[0] if rows else None

    # ──────────────────────────────────────────────────────────────────────────
    # Legacy aliases — kept for backwards compatibility with older call-sites.
    # These delegate to open_pool() / close_pool() so existing code still works.
    # ──────────────────────────────────────────────────────────────────────────

    def connect(self) -> None:
        """Legacy alias for open_pool(). Prefer open_pool() in new code."""
        self.open_pool()

    def close(self) -> None:
        """Legacy alias for close_pool(). Prefer close_pool() in new code."""
        self.close_pool()
