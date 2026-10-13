-- Replaces all non-key fields; pass NULL explicitly to clear a nullable field.
-- @Password must contain an application-generated password hash, never plaintext.
CREATE OR ALTER PROCEDURE [dbo].[User_Update]
    @UserID INT,
    @Username NVARCHAR(50),
    @Email NVARCHAR(255),
    @Password NVARCHAR(255),
    @Bio NVARCHAR(MAX),
    @ProfilePicture NVARCHAR(255)
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;

    UPDATE [dbo].[User]
    SET [Username] = @Username,
        [Email] = @Email,
        [Password] = @Password,
        [Bio] = @Bio,
        [ProfilePicture] = @ProfilePicture
    OUTPUT INSERTED.[UserID], INSERTED.[Username], INSERTED.[Email], INSERTED.[Bio], INSERTED.[ProfilePicture]
    WHERE [UserID] = @UserID;

    IF @@ROWCOUNT = 0
        THROW 50001, 'User was not found.', 1;
END;
