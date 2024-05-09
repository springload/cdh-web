declare module '*.svg' {
  const content: any;
  export default content;
}

declare module '*.scss' {
  const classes: { [key: string]: string };
  export default classes;
}
