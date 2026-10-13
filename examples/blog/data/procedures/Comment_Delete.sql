CREATE OR ALTER PROCEDURE [dbo].[Comment_Delete]
    @CommentID INT
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;

    DELETE FROM [dbo].[Comment]
    OUTPUT DELETED.[CommentID]
    WHERE [CommentID] = @CommentID;

    IF @@ROWCOUNT = 0
        THROW 50001, 'Comment was not found.', 1;
END;
