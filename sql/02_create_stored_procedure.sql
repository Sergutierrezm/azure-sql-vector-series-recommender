CREATE OR ALTER PROCEDURE dbo.SearchSemanticShows
    @queryVector NVARCHAR(MAX),
    @topK INT = 3
AS
BEGIN
    SET NOCOUNT ON;

    -- 1. Tabla temporal para el vector de búsqueda
    DECLARE @QueryTable TABLE (VectorIndex INT, VectorValue FLOAT);
    
    INSERT INTO @QueryTable (VectorIndex, VectorValue)
    SELECT CAST([key] AS INT), CAST([value] AS FLOAT)
    FROM OPENJSON(@queryVector);

    -- 2. Calcular la magnitud del vector de búsqueda una sola vez
    DECLARE @QueryMagnitude FLOAT;
    SELECT @QueryMagnitude = SQRT(SUM(VectorValue * VectorValue)) FROM @QueryTable;

    -- 3. Calcular la Similitud del Coseno completa (Producto Punto / Magnitudes)
    SELECT TOP (@topK)
        s.ShowID,
        s.Title,
        s.Genre,
        s.ReleaseYear,
        s.Synopsis,  -- <-- AÑADIDO PARA LA VERSIÓN 3.0 (FRONTEND)
        (
            SELECT 
                SUM(q.VectorValue * CAST(v.[value] AS FLOAT)) / 
                NULLIF(@QueryMagnitude * SQRT(SUM(CAST(v.[value] AS FLOAT) * CAST(v.[value] AS FLOAT))), 0)
            FROM OPENJSON(s.EmbeddingJson) AS v
            JOIN @QueryTable q ON CAST(v.[key] AS INT) = q.VectorIndex
        ) AS SimilarityScore
    FROM 
        dbo.Shows s
    ORDER BY 
        SimilarityScore DESC;
END;
GO