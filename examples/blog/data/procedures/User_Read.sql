-- Omit @UserID, or pass NULL, to list all rows. Password hashes are not returned.
CREATE OR ALTER PROCEDURE [dbo].[User_Read]
    @UserID INT = NULL
AS
BEGIN
    SET NOCOUNT ON;

    SELECT [UserID], [Username], [Email], [Bio], [ProfilePicture]
    FROM [dbo].[User]
    WHERE @UserID IS NULL OR [UserID] = @UserID
    ORDER BY [UserID];
END;
