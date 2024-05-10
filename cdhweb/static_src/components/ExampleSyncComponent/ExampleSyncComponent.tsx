type Props = {
  pageTitle?: string;
};

const ExampleReactComponent = ({ pageTitle }: Props): JSX.Element => {
  return (
    <div className="example-sync-component">
      This is a React component. Here is a prop: <em>{pageTitle}</em>
    </div>
  );
};

export default ExampleReactComponent;
