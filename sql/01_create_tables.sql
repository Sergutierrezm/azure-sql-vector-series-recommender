USE TVShowDB;
GO

-- Limpieza preventiva
IF OBJECT_ID('dbo.Shows', 'U') IS NOT NULL 
    ALTER TABLE dbo.Shows SET (SYSTEM_VERSIONING = OFF);
DROP TABLE IF EXISTS dbo.Shows;
DROP TABLE IF EXISTS dbo.ShowsHistory;
GO

-- 1. Tabla History para System-Versioning (Auditoría DP-800)
CREATE TABLE dbo.ShowsHistory (
    ShowID INT NOT NULL,
    Title NVARCHAR(100) NOT NULL,
    Genre NVARCHAR(50) NOT NULL,
    ReleaseYear INT NOT NULL,
    Synopsis NVARCHAR(MAX) NOT NULL,
    EmbeddingJson NVARCHAR(MAX) NULL,
    SysStartTime DATETIME2 NOT NULL,
    SysEndTime DATETIME2 NOT NULL
);
GO

-- 2. Tabla Principal de Series (Vector JSON + Temporal Table)
CREATE TABLE dbo.Shows (
    ShowID INT IDENTITY(1,1) PRIMARY KEY,
    Title NVARCHAR(100) NOT NULL,
    Genre NVARCHAR(50) NOT NULL,
    ReleaseYear INT NOT NULL,
    Synopsis NVARCHAR(MAX) NOT NULL,
    EmbeddingJson NVARCHAR(MAX) NULL, -- Almacenamiento vectorial en formato JSON
    SysStartTime DATETIME2 GENERATED ALWAYS AS ROW START NOT NULL,
    SysEndTime DATETIME2 GENERATED ALWAYS AS ROW END NOT NULL,
    PERIOD FOR SYSTEM_TIME (SysStartTime, SysEndTime)
)
WITH (SYSTEM_VERSIONING = ON (HISTORY_TABLE = dbo.ShowsHistory));
GO