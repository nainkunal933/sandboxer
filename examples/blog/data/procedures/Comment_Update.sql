-- Replaces all non-key fields; pass NULL explicitly to clear a nullable field.
CREATE OR ALTER PROCEDURE [dbo].[Comment_Update]
    @CommentID INT,
    @PostID INT,
    @UserID INT,
    @Content NVARCHAR(MAX),
    @Timestamp DATETIME2(7)
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;

    UPDATE [dbo].[Comment]
    SET [PostID] = @PostID,
        [UserID] = @UserID,
        [Content] = @Content,
        [Timestamp] = @Timestamp
    OUTPUT INSERTED.[CommentID], INSERTED.[PostID], INSERTED.[UserID], INSERTED.[Content], INSERTED.[Timestamp]
    WHERE [CommentID] = @CommentID;

    IF @@ROWCOUNT = 0
        THROW 50001, 'Comment was not found.', 1;
END;
