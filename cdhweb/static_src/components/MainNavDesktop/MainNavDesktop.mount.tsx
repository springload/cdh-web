import { createRoot } from 'react-dom/client';
import type { InitComponent } from '../ComponentsInit';
import MainNavDesktop from './MainNavDesktop';
import {
  MainNavDataPrimary,
  MainNavDataPrimarySimplified,
} from '../../data-types';

const initComponent: InitComponent = (componentEl) => {
  // Desktop version only needs primary nav data, not secondary, which is displayed statically above the primary nav.
  const primaryNavDataEl = document.getElementById('navigation-data-primary');

  if (!primaryNavDataEl) {
    throw Error(`Expected component data for main nav. Aborting React render.`);
  }
  const primaryNavData = JSON.parse(
    primaryNavDataEl.innerHTML,
  ) as MainNavDataPrimary;

  // Flatten weirdly-overly-nested data.
  // BED TODO, simplify actual data
  const primaryNavDataSimplified: MainNavDataPrimarySimplified =
    primaryNavData.primary_nav_data.primary_nav.l1_menu_items;

  const searchUrl = componentEl.getAttribute('data-search-url') || '/search';

  const root = createRoot(componentEl);
  root.render(
    <MainNavDesktop
      primaryNavData={primaryNavDataSimplified}
      searchUrl={searchUrl}
      isSearchPage={window.location.pathname === searchUrl}
    />,
  );

  return () => {
    // Return a cleanup function
    root.unmount();
  };
};

export default initComponent;
