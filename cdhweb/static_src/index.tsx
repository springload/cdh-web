import './PublicPath'; // MUST be first (yes, before absolute imports)
import { ComponentsInit } from './components/ComponentsInit';
import './styles.scss';

(function (): void {
  // Init the site's code here
  ComponentsInit();
})();
