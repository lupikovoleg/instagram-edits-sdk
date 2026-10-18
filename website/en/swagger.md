# Swagger & OpenAPI

The reference describes the real transport:

```http
POST https://i.instagram.com/graphql_www
Content-Type: application/x-www-form-urlencoded
```

There are **nine named read-query examples** in one endpoint. Choose an operation
to inspect its persisted query ID, variables and encoded form.

[Open Swagger UI](swagger-ui/index.html){ .md-button .md-button--primary }
[Download OpenAPI JSON](openapi.json){ .md-button }

## What the viewer does

- Displays query variables, request headers and form bodies.
- Shows known schemas and the SDK's normalized snapshot shape.
- Lets you copy examples and download the OpenAPI specification.
- Uses local JS/CSS assets without a CDN.

Request execution and credential entry are disabled. Run real requests in your
backend with the SDK. A public documentation page is not an API gateway.

`variables` is a **JSON string inside the form**, not a nested form object or a
separate REST endpoint. Friendly-name and document-ID headers must match the
selected example.

## Schema scope

Optional and account-dependent response fields are not fully known. The raw
GraphQL schema is deliberately open rather than presenting one observed response
as the complete server schema. See the [data reference](data-reference.md) for
observed fields and [verification](verification.md) for availability.

The viewer's [license](swagger-ui/vendor/LICENSE) and
[asset provenance](swagger-ui/vendor/provenance.json) are included.
