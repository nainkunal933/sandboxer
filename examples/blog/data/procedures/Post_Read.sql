-- Omit @PostID, or pass NULL, to list all rows.
CREATE OR ALTER PROCEDURE [dbo].[Post_Read]
    @PostID INT = NULL
AS
BEGIN
    SET NOCOUNT ON;

    SELECT [PostID], [Title], [Content], [Category], [PublicationDate], [Tags]
    FROM [dbo].[Post]
    WHERE @PostID IS NULL OR [PostID] = @PostID
    ORDER BY [PostID];
END;
