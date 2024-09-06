import type { InitComponent } from '../ComponentsInit';

// The accordion component uses browser native disclosure widgets (detials/summary).
// However, not all browser/screen-reader combinations serve this content well, so
// we add some progressive enhancement below.

const initComponent: InitComponent = (componentEl) => {
  const accordions = componentEl.querySelectorAll('details');

  if (!accordions) {
    throw Error(
      'No accordion items found (details/summary disclosure widgets)',
    );
  }

  // Progressively enhance disclosure widgets
  const addA11yAttributes = (summaryEl: HTMLElement) => {
    summaryEl.setAttribute('role', 'button');

    // Check current state first (on the off-chance one is set to be open by default):
    const isOpenByDefault = summaryEl?.closest('details')?.hasAttribute('open');
    summaryEl.setAttribute('aria-expanded', isOpenByDefault ? 'true' : 'false');
  };

  const toggleA11yState = (
    accordionEl: HTMLElement,
    summaryEl: HTMLElement,
  ) => {
    const isAlreadyOpen = accordionEl.hasAttribute('open');
    summaryEl.setAttribute('aria-expanded', String(!isAlreadyOpen));
  };

  [...accordions].map((accordion) => {
    const summary = accordion.querySelector('summary');
    if (!summary) {
      throw Error(
        'Summary (<summary>) not found for accordion (<details>) item',
      );
    }

    addA11yAttributes(summary);

    summary.addEventListener('click', () =>
      toggleA11yState(accordion, summary),
    );
  });

  return () => {
    // Return a cleanup function. Nothing to do here.
  };
};

export default initComponent;
