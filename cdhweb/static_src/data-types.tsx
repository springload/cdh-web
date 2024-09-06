export type MainNavDataPrimary = {
  primary_nav_data: {
    primary_nav: {
      l1_menu_items: MainNavDataPrimarySimplified;
    };
  };
};

export type MainNavDataPrimarySimplified = MainNavItemPrimary[];

export type MainNavDataSecondary = {
  secondary_nav_data: {
    secondary_nav: MainNavDataSecondarySimplified;
  };
};

export type MainNavDataSecondarySimplified = {
  items: NavItem[];
  cta?: NavItem[];
};

export type MainNavItemPrimary = {
  title: string;
  overview: string;
  link_url: string;
  l2_items: NavItem[];
  isSearch?: boolean;
  is_current: boolean;
};

export type NavItem = {
  title: string;
  link_url: string;
};
