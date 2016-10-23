
-- ******************************************
--       Table: SENSOR
-- Description: List of all available sensors

DROP TABLE IF EXISTS sensor;

CREATE TABLE sensor (
    id INTEGER PRIMARY KEY,
    name TEXT
);

INSERT INTO sensor VALUES (1, 'cpu_load');
INSERT INTO sensor VALUES (2, 'web_server');

-- ******************************************
--       Table: PROBE
-- Description: Adds parameter list to sensor command
--              and defines default thresholds

DROP TABLE IF EXISTS probe;

CREATE TABLE probe (
    id INTEGER PRIMARY KEY,
    sensor_id INTEGER,
    name TEXT,
    parameter TEXT,
    warning FLOAT,
    error FLOAT,
    FOREIGN KEY (sensor_id) REFERENCES sensor(id)
);

INSERT INTO probe VALUES ( 1, 1, 'Used CPU %', 'used', 1.1, 1.3);
INSERT INTO probe VALUES ( 2, 2, 'Received HTTP requests', 'receiver_req', 400, 500);

-- ******************************************
--       Table: HOST
-- Description: List of all monitoring agents

DROP TABLE IF EXISTS host;

CREATE TABLE host (
    id INTEGER PRIMARY KEY,
    name TEXT,
    address TEXT,
    port TEXT
);

INSERT INTO host VALUES (1, 'My laptop', 'localhost', '8080');
INSERT INTO host VALUES (2, 'My server', 'localhost', '8080');

-- ******************************************
--       Table: HOSTPROBE
-- Description: Maps available probes to the hosts
--              overrides thresholds if required

DROP TABLE IF EXISTS hostprobe;

CREATE TABLE hostprobe (
    id INTEGER PRIMARY KEY,
    probe_id INTEGER,
    host_id INTEGER,
    warning FLOAT,
    error FLOAT,
    FOREIGN KEY (probe_id) REFERENCES probe(id),
    FOREIGN KEY (host_id)  REFERENCES host(id)
);


INSERT INTO hostprobe VALUES ( 1,  1, 1, NULL, NULL);
INSERT INTO hostprobe VALUES ( 2,  1, 2, 6.5, 8.5);
INSERT INTO hostprobe VALUES ( 3,  2, 2, 680, 780);

-- ******************************************
--       Table: TICKETQUEUE
-- Description: Holds all pendiing and sent tickets
--              tickets are removed when the sensor reading arrive

DROP TABLE IF EXISTS ticketqueue;

CREATE TABLE ticketqueue (
    id INTEGER PRIMARY KEY,
    hostprobe_id INTEGER,
    timestamp TEXT,
    dispatched INTEGER,
    FOREIGN KEY (hostprobe_id) REFERENCES hostprobe(id)
);

-- ******************************************
--       Table: PROBEREADING
-- Description: Stores all readings obtained from the monitoring agents

DROP TABLE IF EXISTS probereading;

CREATE TABLE probereading (
    id INTEGER PRIMARY KEY,
    hostprobe_id INTEGER,
    timestamp TEXT,
    probe_value FLOAT,
    ret_code INTEGER,
    FOREIGN KEY (hostprobe_id) REFERENCES hostprobe(id)
);

-- ******************************************
--       Table: PROBINGSCHEDULE
-- Description: Defines execution intervals for the probes

DROP TABLE IF EXISTS probingschedule;

CREATE TABLE probingschedule (
    id INTEGER PRIMARY KEY,
    hostprobe_id INTEGER,
    probeinterval INTEGER,
    FOREIGN KEY (hostprobe_id) REFERENCES hostprobe(id)
);

INSERT INTO probingschedule VALUES (1, 1, 1);
INSERT INTO probingschedule VALUES (2, 2, 1);
INSERT INTO probingschedule VALUES (3, 3, 5);

-- ******************************************
--       Table: SYSTEMPARAMS
-- Description: Defines system configuration parameters

DROP TABLE IF EXISTS systemparams;

CREATE TABLE systemparams (
    id INTEGER PRIMARY KEY,
    name TEXT,
    value TEXT
);

INSERT INTO systemparams VALUES (1, 'monitor_url', 'http://localhost:8081/xmlrpc/');

-- ******************************************
--       Table: HOSTPARAMS
-- Description: Assigns system parameters to the hosts
--              allows to override the default values

DROP TABLE IF EXISTS hostparams;

CREATE TABLE hostparams (
    id INTEGER PRIMARY KEY,
    host_id INTEGER,
    param_id INTEGER,
    value TEXT,
    FOREIGN KEY (host_id) REFERENCES host(id),
    FOREIGN KEY (param_id) REFERENCES systemparams(id)
);

INSERT INTO hostparams VALUES (1, 1, 1, 'http://localhost:8081/xmlrpc/');
INSERT INTO hostparams VALUES (2, 2, 1, 'http://localhost:8081/xmlrpc/');

