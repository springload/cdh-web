import type { InitComponent } from '../ComponentsInit';

/**
 * A `<select>` menu which navigates onchange, via a data-href on each `<option>`
 */
const initComponent: InitComponent = (componentEl) => {
  const options = componentEl.querySelectorAll('option');

  if (!options) {
    console.log('No <option> items found. Aborting.');
    return () => {
      //
    };
  }

  componentEl.addEventListener('change', (e: Event) => {
    const target = e.target as HTMLSelectElement;
    const selectedOption = target.options[target.selectedIndex];
    const url = selectedOption.getAttribute('data-href');

    if (!url) {
      console.error('No `data-href` specified for selected option.');
      return;
    }

    window.location.href = url;
  });

  return () => {
    // Return a cleanup function. Nothing to do here.
  };
};

export default initComponent;
