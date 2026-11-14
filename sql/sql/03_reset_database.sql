-- 1. Desactivar auditoría temporal temporalmente
ALTER TABLE dbo.Shows SET (SYSTEM_VERSIONING = OFF);

-- 2. Vaciar las tablas y reiniciar los IDs
TRUNCATE TABLE dbo.Shows;
TRUNCATE TABLE dbo.ShowsHistory;

-- 3. Reactivar la auditoría temporal
ALTER TABLE dbo.Shows SET (SYSTEM_VERSIONING = ON (HISTORY_TABLE = dbo.ShowsHistory));
GO