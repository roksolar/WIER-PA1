CREATE SCHEMA IF NOT EXISTS crawldb;

CREATE TABLE crawldb.data_type ( 
	code                 varchar(20)  NOT NULL,
	CONSTRAINT pk_data_type_code PRIMARY KEY ( code )
 );

CREATE TABLE crawldb.page_type ( 
	code                 varchar(20)  NOT NULL,	
	CONSTRAINT pk_page_type_code PRIMARY KEY ( code )
 );

CREATE TABLE crawldb.site ( 
	id                   serial  NOT NULL,
	"domain"             varchar(500)  ,
	robots_content       text  ,
	sitemap_content      text  ,
	CONSTRAINT pk_site_id PRIMARY KEY ( id )
 );

CREATE TABLE crawldb.page ( 
	id                   serial  NOT NULL,
	site_id              integer  ,
	page_type_code       varchar(20)  ,
	url                  varchar(3000)  ,
	html_content         text  ,
	http_status_code     integer  ,
	accessed_time        timestamp  ,
	html_content_hash    uuid,
	CONSTRAINT pk_page_id PRIMARY KEY ( id ),
	CONSTRAINT unq_url_idx UNIQUE ( url ) 
 );

CREATE INDEX "idx_page_site_id" ON crawldb.page ( site_id );

CREATE INDEX "idx_page_page_type_code" ON crawldb.page ( page_type_code );

CREATE TABLE crawldb.page_data ( 
	id                   serial  NOT NULL,
	page_id              integer  ,
	data_type_code       varchar(20)  ,
	"data"               bytea,
	CONSTRAINT pk_page_data_id PRIMARY KEY ( id )
 );

CREATE INDEX "idx_page_data_page_id" ON crawldb.page_data ( page_id );

CREATE INDEX "idx_page_data_data_type_code" ON crawldb.page_data ( data_type_code );

CREATE TABLE crawldb.image ( 
	id                   serial  NOT NULL,
	page_id              integer  ,
	filename             varchar(10000)  ,
	content_type         varchar(5000)  ,
	"data"               bytea  ,
	accessed_time        timestamp  ,
	CONSTRAINT pk_image_id PRIMARY KEY ( id )
 );

CREATE INDEX "idx_image_page_id" ON crawldb.image ( page_id );

CREATE TABLE crawldb.link ( 
	from_page            integer  NOT NULL,
	to_page              integer  NOT NULL,
	CONSTRAINT _0 PRIMARY KEY ( from_page, to_page )
 );

CREATE INDEX "idx_link_from_page" ON crawldb.link ( from_page );

CREATE INDEX "idx_link_to_page" ON crawldb.link ( to_page );

ALTER TABLE crawldb.image ADD CONSTRAINT fk_image_page_data FOREIGN KEY ( page_id ) REFERENCES crawldb.page( id ) ON DELETE RESTRICT;

ALTER TABLE crawldb.link ADD CONSTRAINT fk_link_page FOREIGN KEY ( from_page ) REFERENCES crawldb.page( id ) ON DELETE RESTRICT;

ALTER TABLE crawldb.link ADD CONSTRAINT fk_link_page_1 FOREIGN KEY ( to_page ) REFERENCES crawldb.page( id ) ON DELETE RESTRICT;

ALTER TABLE crawldb.page ADD CONSTRAINT fk_page_site FOREIGN KEY ( site_id ) REFERENCES crawldb.site( id ) ON DELETE RESTRICT;

ALTER TABLE crawldb.page ADD CONSTRAINT fk_page_page_type FOREIGN KEY ( page_type_code ) REFERENCES crawldb.page_type( code ) ON DELETE RESTRICT;

ALTER TABLE crawldb.page_data ADD CONSTRAINT fk_page_data_page FOREIGN KEY ( page_id ) REFERENCES crawldb.page( id ) ON DELETE RESTRICT;

ALTER TABLE crawldb.page_data ADD CONSTRAINT fk_page_data_data_type FOREIGN KEY ( data_type_code ) REFERENCES crawldb.data_type( code ) ON DELETE RESTRICT;

INSERT INTO crawldb.data_type VALUES 
	('PDF'),
	('DOC'),
	('DOCX'),
	('PPT'),
	('PPTX');

INSERT INTO crawldb.page_type VALUES 
	('HTML'),
	('BINARY'),
	('DUPLICATE'),
	('FRONTIER'),
	('TIMEOUT');

INSERT INTO crawldb.site (id, domain) VALUES
    (1, 'evem.gov.si'),
    (2, 'e-uprava.gov.si'),
	(3, 'podatki.gov.si'),
	(4, 'e-prostor.gov.si'),
	(5, 'eugo.gov.si'),
	(6, 'mju.gov.si'),
	(7, 'mizs.gov.si'),
	(8, 'portal.evs.gov.si'),
	(9, 'fu.gov.si');

INSERT INTO crawldb.page (site_id, page_type_code, url) VALUES
    (1, 'FRONTIER', 'evem.gov.si'),
    (2, 'FRONTIER', 'e-uprava.gov.si'),
	(3, 'FRONTIER', 'podatki.gov.si'),
	(4, 'FRONTIER', 'e-prostor.gov.si'),
	(5, 'FRONTIER', 'eugo.gov.si'),
	(6, 'FRONTIER', 'mju.gov.si'),
	(7, 'FRONTIER', 'mizs.gov.si'),
	(8, 'FRONTIER', 'portal.evs.gov.si'),
	(9, 'FRONTIER', 'fu.gov.si');