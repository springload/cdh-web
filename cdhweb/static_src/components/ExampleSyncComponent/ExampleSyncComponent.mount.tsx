import { createRoot } from 'react-dom/client';
import type { InitComponent } from '../ComponentsInit';
import ExampleReactComponent from './ExampleSyncComponent';

const initComponent: InitComponent = (componentEl, data) => {
  if (typeof data !== 'string' && data !== undefined) {
    console.error({ data });
    throw Error(
      `Expected component data of string|undefined but received ${typeof data}. See console`,
    );
  }

  const root = createRoot(componentEl);
  root.render(<ExampleReactComponent pageTitle={data} />);

  return () => {
    // Return a cleanup function
    root.unmount();
  };
};

export default initComponent;
