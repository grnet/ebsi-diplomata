import App from '@digigov/nextjs/App';
import initI18n from '@digigov/nextjs/i18n';
import el from 'ui/locales/el';
import en from 'ui/locales/en';
import 'tailwindcss/tailwind.css';
import '../../index.css';

initI18n({
  el: {
    translation: el,
  },
  en: {
    translation: en,
  },
});
export default App;
