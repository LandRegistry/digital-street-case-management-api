-- Creates database for use by the app
CREATE DATABASE casemanagementadb;
CREATE DATABASE casemanagementbdb;
-- Creates user that the app will use under normal day to day running.
-- It has no permissions by default; they will have to be specifically
-- granted in the alembic files when tables are created.
CREATE ROLE conveyancerauser WITH LOGIN PASSWORD 'conveyancerapassword';
CREATE ROLE conveyancerbuser WITH LOGIN PASSWORD 'conveyancerbpassword';
