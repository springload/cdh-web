import { createRoot } from 'react-dom/client';
import type { InitComponent } from '../ComponentsInit';
import MainNavMobile from './MainNavMobile';
import {
  MainNavDataPrimary,
  MainNavDataPrimarySimplified,
  MainNavDataSecondary,
  MainNavDataSecondarySimplified,
} from '../../data-types';

const initComponent: InitComponent = (componentEl) => {
  const primaryNavDataEl = document.getElementById('navigation-data-primary');
  const secondaryNavDataEl = document.getElementById(
    'navigation-data-secondary',
  );
  if (!primaryNavDataEl || !secondaryNavDataEl) {
    throw Error(`Expected component data for main nav. Aborting React render.`);
  }
  const primaryNavData = JSON.parse(
    primaryNavDataEl.innerHTML,
  ) as MainNavDataPrimary;
  const secondaryNavData = JSON.parse(
    secondaryNavDataEl.innerHTML,
  ) as MainNavDataSecondary;

  // Flatten weirdly-overly-nested data.
  // BED TODO, simplify actual data
  const primaryNavDataSimplified: MainNavDataPrimarySimplified =
    primaryNavData.primary_nav_data.primary_nav.l1_menu_items;

  const secondaryNavDataSimplified: MainNavDataSecondarySimplified =
    secondaryNavData.secondary_nav_data.secondary_nav;

  const root = createRoot(componentEl);
  root.render(
    <MainNavMobile
      primaryNavData={primaryNavDataSimplified}
      secondaryNavData={secondaryNavDataSimplified}
    />,
  );

  return () => {
    // Return a cleanup function
    root.unmount();
  };
};

export default initComponent;
