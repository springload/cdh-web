import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';

import ExampleReactComponent from './ExampleSyncComponent';

// React Testing Library docs
// https://testing-library.com/docs/react-testing-library/

test('React testing library example of selecting text', () => {
  const pageTitle = 'a custom page title';
  render(<ExampleReactComponent pageTitle={pageTitle} />);
  const pageTitleContainer = screen.getByText(pageTitle);
  expect(pageTitleContainer).toBeTruthy();
});

test("React testing library example of selecting text that doesn't exist", () => {
  render(<ExampleReactComponent pageTitle="a custom page title" />);
  expect(() => screen.getByText("text that doesn't exist")).toThrow();
});
