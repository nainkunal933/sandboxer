-- @Password must contain an application-generated password hash, never plaintext.
CREATE OR ALTER PROCEDURE [dbo].[User_Create]
    @UserID INT,
    @Username NVARCHAR(50) = NULL,
    @Email NVARCHAR(255) = NULL,
    @Password NVARCHAR(255) = NULL,
    @Bio NVARCHAR(MAX) = NULL,
    @ProfilePicture NVARCHAR(255) = NULL
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;

    INSERT INTO [dbo].[User] ([UserID], [Username], [Email], [Password], [Bio], [ProfilePicture])
    OUTPUT INSERTED.[UserID], INSERTED.[Username], INSERTED.[Email], INSERTED.[Bio], INSERTED.[ProfilePicture]
    VALUES (@UserID, @Username, @Email, @Password, @Bio, @ProfilePicture);
END;
