-- Initial database setup script
-- This script runs when the PostgreSQL container starts for the first time

-- Create the database if it doesn't exist (handled by POSTGRES_DB env var)
-- Create the user if it doesn't exist (handled by POSTGRES_USER env var)

-- Additional setup can be added here if needed
-- For example: extensions, additional schemas, etc.

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Set timezone
SET timezone = 'UTC';