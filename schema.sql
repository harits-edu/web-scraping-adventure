CREATE TABLE IF NOT EXISTS "jobs" (
    "id" INTEGER,
    "position" TEXT NOT NULL,
    "company" TEXT,
    "link" TEXT UNIQUE,
    "date_found" TEXT NOT NULL,
    "job_site" TEXT,
    PRIMARY KEY("id")
);