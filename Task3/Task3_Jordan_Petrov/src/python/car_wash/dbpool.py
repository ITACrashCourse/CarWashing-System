"""DB pool manager.
It is module that describes steps to connect to DB.
It uses pool of connection to avoid load on DB side.
"""

import logging
import time
from contextlib import contextmanager
from threading import Lock

import psycopg2

from car_wash.config import READ_ONLY_USER, READ_WRITE_USER
from car_wash.utils import SingletonMeta


class DBPoolBase(metaclass=SingletonMeta):
    """Base class of DB pool."""

    def _create_connection(self) -> psycopg2.connect:
        """Create connection to DB"""
        raise NotImplementedError('No code added into _create_connection method')

    def _get_connection(self) -> psycopg2.connect:
        """Get connection from pool"""
        raise NotImplementedError('No code added into _get_connection method')

    def _put_connection(self, conn: psycopg2.connect) -> None:
        """Put connection back to pool"""
        raise NotImplementedError('No code added into _put_connection method')


class RODBPool(DBPoolBase):
    """Read only pool of connections."""

    def __init__(self, hostname: str, password: str, username: str, _dbname: str, pool_size: int) -> None:
        """Constructor of RODBPool connections

        :Parameters:
            - `hostname` - DB hostname
            - `password` - DB password
            - `username` - DB username
            - `_dbname` - DB name
            - `pool_size` - size of pool
        """
        super().__init__()
        self._pool = []
        self._hostname = hostname
        self._password = password
        self._username = username
        self._dbname = _dbname
        self._pool_size = pool_size
        self._conn_created = 0
        self._log = logging.getLogger('ro_db_pool')
        self._lock = Lock()

    def _create_connection(self) -> psycopg2.connect:
        """Create connection to DB"""
        return psycopg2.connect(dbname=self._dbname,
                                user=self._username,
                                password=self._password,
                                host=self._hostname)

    def _get_connection(self) -> psycopg2.connect:
        """Get connection from pool"""
        connection = None
        while not connection:
            with self._lock:
                if len(self._pool) > 0:
                    connection = self._pool.pop()
                else:
                    if self._conn_created < self._pool_size:
                        connection = self._create_connection()
                        self._conn_created += 1
                    else:
                        self._log.info('No connections available. Wait 0.1 second.')
                        time.sleep(0.1)

        return connection

    def _put_connection(self, conn: psycopg2.connect) -> None:
        """Put connection back to pool"""
        self._pool.append(conn)

    @contextmanager
    def connection(self):
        """
        Context manager for the read only pool.
        Use cursor to execute queries.
        """
        conn = self._get_connection()
        cursor_ = conn.cursor()
        try:
            yield cursor_
        except psycopg2.Error as err:
            self._log.error('Issue during work with db: %s', err)
            conn.close()
            raise psycopg2.Error('Invalid query.')
        else:
            self._put_connection(conn)
        finally:
            cursor_.close()


class RWDBPool(DBPoolBase):
    """Read only pool of connections."""

    def __init__(self, hostname: str, password: str, username: str, _dbname: str, pool_size: int) -> None:
        """Constructor of RODBPool connections

        :Parameters:
            - `hostname` - DB hostname
            - `password` - DB password
            - `username` - DB username
            - `_dbname` - DB name
            - `pool_size` - size of pool
        """
        super().__init__()
        self._pool = []
        self._hostname = hostname
        self._password = password
        self._username = username
        self._dbname = _dbname
        self._pool_size = pool_size
        self._conn_created = 0
        self._log = logging.getLogger('rw_db_pool')
        self._lock = Lock()

    def _create_connection(self) -> psycopg2.connect:
        """Create connection to DB"""
        return psycopg2.connect(dbname=self._dbname,
                                user=self._username,
                                password=self._password,
                                host=self._hostname)

    def _get_connection(self) -> psycopg2.connect:
        """Get connection from pool"""
        connection = None
        while not connection:
            with self._lock:
                if len(self._pool) > 0:
                    connection = self._pool.pop()
                else:
                    if self._conn_created < self._pool_size:
                        connection = self._create_connection()
                        self._conn_created += 1
                    else:
                        self._log.info('No connections available. Wait 0.1 second.')
                        time.sleep(0.1)

        return connection

    def _put_connection(self, conn: psycopg2.connect) -> None:
        """Put connection back to pool"""
        self._pool.append(conn)

    @contextmanager
    def transaction(self):
        """
        Context manager for the read write pool.
        Use cursor to execute queries.
        """
        conn = self._get_connection()
        cursor_ = conn.cursor()
        try:
            yield cursor_
        except psycopg2.Error as err:
            self._log.error('Issue during work with db: %s', err)
            conn.close()
            raise psycopg2.Error('Invalid query.')
        else:
            conn.commit()
            self._put_connection(conn)
        finally:
            cursor_.close()


# Initialization of RO pool object
ro_db_pool = RODBPool(**READ_ONLY_USER)
# Initialization of RW pool object
rw_db_pool = RWDBPool(**READ_WRITE_USER)