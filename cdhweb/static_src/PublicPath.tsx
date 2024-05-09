/**
 * This file MUST be imported first.
 *
 * Webpack does not know where to find its build assets
 * when it's served from a different domain, which we
 * normally do with CDNs.
 *
 * However Webpack allows us to dynamically configure
 * a CDN prefix by setting __webpack_public_path__
 * before any lazy-loading / code-splitting occurs.
 *
 * See https://webpack.js.org/concepts/output/#advanced
 *
 * We usually have this CDN prefix available in our HTML
 * templating, so in our HTML template we'd render
 * something like,
 *
 * <script> window.staticRoot = {{CDN_PREFIX}}; </script>
 *
 * See pages/templates_src/base.html for an example.
 *
 * ...where {{CDN_PREFIX}} is a template variable, and we
 * set that on window so that's globally available.
 *
 * Finally, we set __webpack_public_path__ to that global
 * here:
 **/
// @ts-ignore
__webpack_public_path__ = window.staticRoot;
