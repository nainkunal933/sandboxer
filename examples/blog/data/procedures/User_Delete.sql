-- Existing foreign keys prevent deletion while comments or interactions reference this row.
CREATE OR ALTER PROCEDURE [dbo].[User_Delete]
    @UserID INT
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;

    DELETE FROM [dbo].[User]
    OUTPUT DELETED.[UserID]
    WHERE [UserID] = @UserID;

    IF @@ROWCOUNT = 0
        THROW 50001, 'User was not found.', 1;
END;
