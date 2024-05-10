import exampleSyncComponent from './ExampleSyncComponent/ExampleSyncComponent.mount';
/**
 * This is where the page is hydrated with types of components.
 *
 * There are two options for types of components: async or sync.
 *
 *  - Async means it's a lazy-loaded component (loaded on demand).
 *    The import would look like,
 *
 *      import('./MyComponent/MyComponent');
 *
 *    That component should have a default export to mount the
 *    component (example code in `./ExampleAsyncComponent`).
 *
 *    If the component isn't on every page, then it should
 *    probably be Async so that users can avoid downloading it
 *    until necessary. See also
 *    https://webpack.js.org/guides/code-splitting/
 *
 *  - Sync means it's NOT lazy loaded and it's always included
 *    in the main JavaScript bundle. You would import the file
 *    using a syntax like
 *
 *      import { MyComponent } from './MyComponent/MyComponent';
 *
 *    If the component loads on every page, especially if it's near
 *    the top (like a primary nav), then it should probably be Sync.
 *    Sync components are included in the top-level JS bundle.
 *
 *
 * Add new component types to the switch/case below.
 *
 */

async function ComponentInit(
  componentEl: HTMLElement,
): Promise<CleanupFunction> {
  const componentName = componentEl.getAttribute(COMPONENT_ATTRIBUTE_NAME);
  if (!componentName) {
    console.error({ componentEl });
    throw Error(`Container requires ${COMPONENT_ATTRIBUTE_NAME} attribute.`);
  }

  let componentConfig = componentEl.querySelector(
    'script[data-component-config]',
  );
  if (componentConfig) {
    componentConfig = JSON.parse(componentConfig.innerHTML);
  }

  const mountAsyncComponent = async (
    asyncComponent: AsyncInitComponent,
  ): Promise<CleanupFunction> =>
    (await asyncComponent).default(componentEl, componentConfig);

  const mountSyncComponent = async (
    initComponent: InitComponent,
  ): Promise<CleanupFunction> => initComponent(componentEl, componentConfig);

  switch (componentName) {
    /**
     * ADD NEW COMPONENTS HERE
     */
    case 'example-async-component':
      return mountAsyncComponent(
        import(
          './ExampleAsyncComponent/ExampleAsyncComponent.mount'
          /* webpackChunkName: "custom-webpack-bundle-filename" */
        ),
      );
    case 'example-sync-component':
      return mountSyncComponent(exampleSyncComponent);
  }

  throw Error(
    `Unrecognised component ${COMPONENT_ATTRIBUTE_NAME}="${componentName}"`,
  );
}

const COMPONENT_ATTRIBUTE_NAME = 'data-component';

// It's possible for components to appear inside other components. The most common example of this
// is things like tooltips that appear, inside accordions on the qualification templates.
// We need to NOT mount these components here.
// Instead, we pass ComponentsInit to the parent component (e.g. accordion.tsx) and run it over
// the scraped HTML in a useEffect. See accordion.tsx for an example.
const filterNestedComponents = (
  componentEl: HTMLElement,
  containerEl: HTMLElement,
): boolean => {
  const parentNode = componentEl.parentElement;
  if (!parentNode) {
    return true;
  }

  const closestComponent = parentNode.closest(`[${COMPONENT_ATTRIBUTE_NAME}]`);
  const containerParents: Element[] = [];
  let containerParent: Element | null = containerEl;
  while (containerParent) {
    containerParents.unshift(containerParent);
    containerParent = containerParent.parentElement;
  }

  const closestComponentIsAncestorOfContainer = containerParents.some(
    (containerParent) => containerParent === closestComponent,
  );

  if (closestComponent && !closestComponentIsAncestorOfContainer) {
    console.info(
      componentEl,
      'was ignored because it is nested inside',
      closestComponent,
    );
    return false;
  }
  return true;
};

export const ComponentsInit = async (
  containerEl: HTMLElement = document.body,
): Promise<CleanupFunction[]> =>
  Promise.all(
    Array.from(
      containerEl.querySelectorAll<HTMLElement>(
        `[${COMPONENT_ATTRIBUTE_NAME}]`,
      ),
    )
      .filter((componentEl) => filterNestedComponents(componentEl, containerEl))
      .map((componentEl) => ComponentInit(componentEl)),
  );

export type AsyncInitComponent = Promise<{ default: InitComponent }>;

export type InitComponent = (
  container: HTMLElement,
  componentData?: unknown,
) => CleanupFunction;

export type CleanupFunction = () => void;
