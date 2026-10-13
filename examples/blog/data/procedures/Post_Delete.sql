-- Existing foreign keys prevent deletion while comments or interactions reference this row.
CREATE OR ALTER PROCEDURE [dbo].[Post_Delete]
    @PostID INT
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;

    DELETE FROM [dbo].[Post]
    OUTPUT DELETED.[PostID]
    WHERE [PostID] = @PostID;

    IF @@ROWCOUNT = 0
        THROW 50001, 'Post was not found.', 1;
END;
