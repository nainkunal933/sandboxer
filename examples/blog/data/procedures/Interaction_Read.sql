-- Omit @InteractionID, or pass NULL, to list all rows.
CREATE OR ALTER PROCEDURE [dbo].[Interaction_Read]
    @InteractionID INT = NULL
AS
BEGIN
    SET NOCOUNT ON;

    SELECT [InteractionID], [UserID], [PostID], [Type], [Timestamp]
    FROM [dbo].[Interaction]
    WHERE @InteractionID IS NULL OR [InteractionID] = @InteractionID
    ORDER BY [InteractionID];
END;
