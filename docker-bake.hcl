// this is cache definition used for caching purposes only
variable "CACHE" { default = "" }
// this is remote registry to push to
variable "REGISTRY" { default = "" }
variable "ENVIRONMENT" { default = "preview" }
variable "PROJECT" { default = "cdhweb" }
variable "VERSION" { default = "latest" }

// targets in groups are built in parallel
group "default" {
  targets = ["tasks", "app"]
}

group "testing" {
  targets = ["app-test"]
}

target "app" {
  dockerfile = "docker/application/Dockerfile"
  target     = "app"
  cache-from = notequal("", CACHE) ? ["${CACHE},name=app"] : []
  cache-to   = notequal("", CACHE) ? ["${CACHE},mode=max,name=app"] : []

  args = {
    VERSION : VERSION,
  }

  tags = notequal("", REGISTRY) ? [
    "${REGISTRY}/${PROJECT}-app:${ENVIRONMENT}-latest",
    "${REGISTRY}/${PROJECT}-app:${ENVIRONMENT}-${VERSION}",
    "${REGISTRY}/${PROJECT}-app:common-${VERSION}",
  ] : []
}

target "app-test" {
  dockerfile = "docker/application/Dockerfile"
  target     = "app-test"
  cache-from = notequal("", CACHE) ? ["${CACHE},name=app-test", "${CACHE},name=base"] : []
  cache-to   = notequal("", CACHE) ? ["${CACHE},mode=max,name=app-test"] : []

  args = {
    VERSION : VERSION,
  }

  // this tag is different as we're going to load it
  tags = ["${PROJECT}/app-test:${VERSION}"]
}

target "tasks" {
  dockerfile = "docker/application/Dockerfile"
  target     = "tasks"
  cache-from = notequal("", CACHE) ? ["${CACHE},name=tasks"] : []
  cache-to   = notequal("", CACHE) ? ["${CACHE},mode=max,name=tasks"] : []

  args = {
    VERSION : VERSION,
  }

  tags = notequal("", REGISTRY) ? [
    "${REGISTRY}/${PROJECT}-tasks:${ENVIRONMENT}-latest",
    "${REGISTRY}/${PROJECT}-tasks:${ENVIRONMENT}-${VERSION}",
    "${REGISTRY}/${PROJECT}-tasks:common-${VERSION}",
  ] : []
}
