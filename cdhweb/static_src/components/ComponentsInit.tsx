import MainNavMobile from './MainNavMobile/MainNavMobile.mount';
import MainNavDesktop from './MainNavDesktop/MainNavDesktop.mount';

/**
 * This is where the page is hydrated with types of components.
 *
 * There are two options for types of components: async or sync.
 *
 *  - `Async` means it's a lazy-loaded component (loaded on demand).
 *    If the component isn't on every page, then it should
 *    probably be Async so that users can avoid downloading it
 *    until necessary. See also
 *    https://webpack.js.org/guides/code-splitting/
 *
 *  - `Sync` means it's NOT lazy loaded and it's always included
 *    in the main JavaScript bundle.
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
    case 'main-nav-mobile':
      return mountSyncComponent(MainNavMobile);

    case 'main-nav-desktop':
      return mountSyncComponent(MainNavDesktop);

    case 'accordion':
      return mountAsyncComponent(
        import(
          './Accordion/Accordion.mount'
          /* webpackChunkName: "component-accordion" */
        ),
      );
    case 'select-navigator':
      return mountAsyncComponent(
        import(
          './SelectNavigator/SelectNavigator'
          /* webpackChunkName: "component-select-navigator" */
        ),
      );
  }

  throw Error(
    `Unrecognised component ${COMPONENT_ATTRIBUTE_NAME}="${componentName}"`,
  );
}

const COMPONENT_ATTRIBUTE_NAME = 'data-component';

export const ComponentsInit = async (
  containerEl: HTMLElement = document.body,
): Promise<CleanupFunction[]> =>
  Promise.all(
    Array.from(
      containerEl.querySelectorAll<HTMLElement>(
        `[${COMPONENT_ATTRIBUTE_NAME}]`,
      ),
    ).map((componentEl) => ComponentInit(componentEl)),
  );

export type AsyncInitComponent = Promise<{ default: InitComponent }>;

export type InitComponent = (
  container: HTMLElement,
  componentData?: unknown,
) => CleanupFunction;

export type CleanupFunction = () => void;
