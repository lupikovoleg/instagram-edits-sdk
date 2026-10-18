/* Local documentation viewer. Does not accept credentials or send API requests. */
window.ui = SwaggerUIBundle({
  url: "../openapi.json",
  dom_id: "#swagger-ui",
  presets: [SwaggerUIBundle.presets.apis],
  layout: "BaseLayout",
  supportedSubmitMethods: [],
  persistAuthorization: false,
  validatorUrl: null,
  deepLinking: true,
  docExpansion: "list",
  defaultModelsExpandDepth: 0,
  showExtensions: false,
  requestInterceptor: function (request) {
    var target = new URL(request.url, window.location.href);
    if (target.origin !== window.location.origin || !target.pathname.endsWith("/openapi.json")) {
      throw new Error("This read-only viewer only loads the local OpenAPI specification.");
    }
    return request;
  }
});

// Swagger renders URL-encoded request schemas but not a read-only example picker.
// Display those same OpenAPI examples explicitly; never accept credentials here.
fetch("../openapi.json").then(function (response) {
  if (!response.ok) throw new Error("Cannot load local specification");
  return response.json();
}).then(function (spec) {
  var examples = spec.paths["/graphql_www"].post.requestBody.content["application/x-www-form-urlencoded"].examples;
  var choice = document.getElementById("query-choice");
  Object.keys(examples).forEach(function (name) {
    var option = document.createElement("option");
    option.value = name; option.textContent = name; choice.appendChild(option);
  });
  function render() {
    var example = examples[choice.value];
    var form = example.value;
    document.getElementById("query-observation").textContent = example.description;
    document.getElementById("query-payload").textContent =
      "POST https://i.instagram.com/graphql_www\n" +
      "X-FB-Friendly-Name: " + form.fb_api_req_friendly_name + "\n" +
      "X-Client-Doc-Id: " + form.client_doc_id + "\n" +
      "Content-Type: application/x-www-form-urlencoded\n\n" +
      "Decoded variables (serialize as a JSON string in the form):\n" +
      JSON.stringify(JSON.parse(form.variables), null, 2) + "\n\n" +
      "URL-encoded request body (authentication headers omitted):\n" +
      new URLSearchParams(form).toString();
  }
  choice.addEventListener("change", render);
  render();
}).catch(function () {
  document.getElementById("query-observation").textContent = "Open this viewer through the local HTTP server described in swagger.md.";
});
