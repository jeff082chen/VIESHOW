CREATE TABLE activities (
    UID                    CHAR(24)        NOT NULL,
    title                  VARCHAR(128)    NOT NULL,
    category               BIT(3)          NOT NULL      CHECK (category in (1, 2, 3, 6)),
    startDate              DATE            NOT NULL,
    endDate                DATE            NOT NULL,
    sourceWebName          VARCHAR(64)     NOT NULL,
    showUnit               VARCHAR(256),
    discountInfo           VARCHAR(2048),
    descriptionFilterHtml  TEXT,
    imageUrl               VARCHAR(256),
    webSales               VARCHAR(128),
    sourceWebPromote       VARCHAR(128),
    likeCount              INT                           DEFAULT (0),
    PRIMARY KEY (UID)
);

CREATE TABLE shows (
    UID                    CHAR(24)        NOT NULL,
    startTime              DATETIME(0)     NOT NULL,
    endTime                DATETIME(0),
    onSales                BOOLEAN         NOT NULL,
    location               VARCHAR(128),
    locationName           VARCHAR(128),
    latitude               FLOAT,
    longitude              FLOAT,
    PRIMARY KEY (UID, startTime),
    FOREIGN KEY (UID) REFERENCES activities(UID)
);

CREATE TABLE reply (
    id                     INT             NOT NULL,
    UID                    CHAR(24)        NOT NULL,
    member_id              VARCHAR(20)     NOT NULL,
    content                TEXT            NOT NULL,
    likeCount              INT                           DEFAULT (0),
    PRIMARY KEY (id, UID),
    FOREIGN KEY (UID) REFERENCES activities(UID),
    FOREIGN KEY (menber_id) REFERENCES members(member_id)
);

CREATE TABLE team (
    id                     INT             NOT NULL,
    UID                    CHAR(24)        NOT NULL,
    member_id              VARCHAR(20)     NOT NULL,
    place                  VARCHAR(256)    NOT NULL,
    contact                VARCHAR(256)    NOT NULL,
    PRIMARY KEY (id, UID),
    FOREIGN KEY (UID) REFERENCES activities(UID),
    FOREIGN KEY (menber_id) REFERENCES members(member_id)
);

CREATE TABLE restaurant (
    latitude               FLOAT           NOT NULL,
    longitude              FLOAT           NOT NULL,
    type                   VARCHAR(256),
    name                   VARCHAR(256),
    address                VARCHAR(256),
    city                   VARCHAR(64),
    area                   VARCHAR(64),
    PRIMARY KEY (latitude, longitude, name)
);

CREATE TABLE favorites (
    UID                    CHAR(24)        NOT NULL,
    member_id              VARCHAR(20)     NOT NULL,
    PRIMARY KEY (UID, menber_id),
    FOREIGN KEY (UID) REFERENCES activities(UID),
    FOREIGN KEY (menber_id) REFERENCES members(member_id)
);

CREATE TABLE members (
    member_id              VARCHAR(20)     NOT NULL,
    password               VARCHAR(20)     NOT NULL,
    PRIMARY KEY (member_id)
);