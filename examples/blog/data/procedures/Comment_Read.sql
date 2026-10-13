-- Omit @CommentID, or pass NULL, to list all rows.
CREATE OR ALTER PROCEDURE [dbo].[Comment_Read]
    @CommentID INT = NULL
AS
BEGIN
    SET NOCOUNT ON;

    SELECT [CommentID], [PostID], [UserID], [Content], [Timestamp]
    FROM [dbo].[Comment]
    WHERE @CommentID IS NULL OR [CommentID] = @CommentID
    ORDER BY [CommentID];
END;
