# Credentials and private data

Report credential exposure privately to the repository maintainer; do not paste
tokens into an issue. This repository does not operate an authentication service.

Session credentials belong in your secret manager or a local ignored file.
Exports can contain personal analytics and signed media URLs. Do not commit them.
If a credential was exposed, end the relevant Instagram session using Instagram's
account controls and replace the credential in your service.

The client verifies TLS, does not follow redirects with credentials, bounds
response sizes and timeouts, and does not log request headers. It does not bypass
Instagram account challenges or implement arbitrary-target HTTP requests.
