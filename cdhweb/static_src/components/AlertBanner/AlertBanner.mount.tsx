import { InitComponent } from '../ComponentsInit';

const initComponent: InitComponent = (component) => {
  const alertId = component.getAttribute('data-alert-id');
  if (!alertId) {
    throw Error('No banner alert ID supplied');
  }
  const alertHasBeenDismissed = !!localStorage.getItem(alertId);

  if (alertHasBeenDismissed)
    return () => {
      // Alert has previously been dismissed. No need to show it. Abort.
    };

  component.classList.remove('u-hidden');
  const dismissBtn = component.querySelector('button');

  dismissBtn?.addEventListener('click', () => {
    localStorage.setItem(alertId, alertId);
    component.classList.add('u-hidden');
  });

  return () => {
    // Return a cleanup function
    // nothing to do in this case;
  };
};

export default initComponent;
