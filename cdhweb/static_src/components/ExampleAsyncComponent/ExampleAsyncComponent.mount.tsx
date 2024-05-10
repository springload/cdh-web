import { createRoot } from 'react-dom/client';
import type { InitComponent } from '../ComponentsInit';
import ExampleReactComponent from './ExampleAsyncComponent';

const initComponent: InitComponent = (componentEl, data) => {
  if (typeof data !== 'string') {
    throw Error('Expected data of type string');
  }

  const root = createRoot(componentEl);
  root.render(<ExampleReactComponent pageTitle={data} />);

  return () => {
    // Return a cleanup function
    root.unmount();
  };
};

export default initComponent;
