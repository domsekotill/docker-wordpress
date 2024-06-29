Feature: S3 Media Uploads
	When an S3 bucket is configured for user-uploaded media, media should be
	pushed to the bucket during an upload; requests for the media either
	proxied or provided with a URL at the bucket; and pre-existing media
	uploaded during container startup to facilitate migrations.

	Scenario: Pre-existing media in the uploads directory is uploaded to a path bucket
		Given the site is not running
		And the site is configured to use S3 with path buckets
		And /app/media/some-content.txt exists in the backend
		When the site is started
		Then the S3 bucket has some-content.txt

	Scenario: Pre-existing media in the uploads directory is uploaded to a subdomain bucket
		Given the site is not running
		And the site is configured to use S3 with subdomain buckets
		And /app/media/some-content.txt exists in the backend
		When the site is started
		Then the S3 bucket has some-content.txt
