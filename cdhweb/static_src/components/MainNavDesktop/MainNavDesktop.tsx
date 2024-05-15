import DesktopMenuItem from './MainNavDesktopItem';
import { MainNavDataPrimarySimplified } from '../../data-types';
import { MouseEvent, createRef, useEffect, useRef, useState } from 'react';

type DesktopMenuDataType = {
  primaryNavData: MainNavDataPrimarySimplified;
  searchUrl: string;
};

const DesktopMenu = ({
  primaryNavData,
  searchUrl,
}: DesktopMenuDataType): JSX.Element => {
  const [currentOpenIndex, setCurrentOpenIndex] = useState(-1);

  // Put a "hard-coded" search menu item into the mix
  const navDataPlusSearch = [
    ...primaryNavData,
    {
      isSearch: true,
      title: 'Search',
      overview: 'Search our website for people, projects, events or blogs.',
      l2_items: [],
      link_url: searchUrl,
    },
  ];

  const dropdownRefs = useRef(
    navDataPlusSearch.map(() => createRef<HTMLDivElement>()),
  );

  // Check for clicks outside the megamenu, to see if we should close it.
  // Fired on all clicks. Except on the top level anchor link, where toggleDropdown
  // stops it via a stopPropagation().
  const handleClick = (e: globalThis.MouseEvent) => {
    setCurrentOpenIndex((currentOpenIndex) => {
      // if a dropdown is already open...
      if (currentOpenIndex > -1) {
        // if the click was INSIDE an open megamenu, do nothing
        if (
          dropdownRefs?.current[currentOpenIndex].current?.contains(
            e.target as HTMLElement,
          )
        ) {
          return currentOpenIndex;
        }
      }
      //  if click was OUTSIDE an open megamenu, close the menu
      return -1;
    });
  };

  useEffect(() => {
    window.addEventListener('click', handleClick);
    return () => {
      window.removeEventListener('click', handleClick);
    };
  }, []);

  const toggleDropdown = (e: MouseEvent<HTMLElement>, index: number) => {
    // If it was a keyboard event, bypass all the other jazz
    if (!e) {
      setCurrentOpenIndex(-1);
      return;
    }

    e.stopPropagation(); // don't run global click listener (handleClick)

    setCurrentOpenIndex((currentOpenIndex) => {
      return currentOpenIndex === index ? -1 : index;
    });
  };

  // Handle escape key and focus
  useEffect(() => {
    const handleKeys = (event: KeyboardEvent) => {
      if (event.key !== 'Escape' && event.key !== 'Tab') return;

      // Handle escape key (close menu)
      if (event.key === 'Escape') {
        setCurrentOpenIndex(-1);
      }
      // Handle tab key (close menu when focus out).
      // - shift+tab on the FIRST item should close the menu.
      // - tab (but not shift+tab) on the LAST item should close the menu.
      if (
        event.key === 'Tab' &&
        // Typescript stuff
        (event.target instanceof HTMLAnchorElement ||
          event.target instanceof HTMLButtonElement ||
          event.target instanceof HTMLInputElement) &&
        // Checking for tabbing back from first item, or forward from last item
        ((event.target.dataset.isLast && !event.shiftKey) ||
          (event.target.dataset.isFirst && event.shiftKey))
      ) {
        // Restore focus to the original dropdown element.
        const parentNavItem = event.target.closest(
          '.main-nav-desktop__main-item',
        );
        if (parentNavItem) {
          const closestNavItemLink = parentNavItem.querySelector(
            '.main-nav-desktop__item',
          );

          if (closestNavItemLink) {
            closestNavItemLink &&
              (closestNavItemLink as HTMLButtonElement).focus();
          }
        }

        setCurrentOpenIndex(-1);
      }
    };
    window.addEventListener('keydown', handleKeys);

    return () => {
      window.removeEventListener('keydown', handleKeys);
    };
  }, [setCurrentOpenIndex]);

  return (
    <ul className="main-nav-desktop__list">
      {navDataPlusSearch.map((item, i) => (
        // BED TODO! We'll need a isCurrentPage/isCurrentSection thing added to
        // the data blob, to highlight the current menu item.
        <DesktopMenuItem
          key={i}
          item={item}
          isOpen={i === currentOpenIndex}
          onClick={(e: MouseEvent<HTMLElement>) => toggleDropdown(e, i)}
          dropdownRef={dropdownRefs.current[i]}
        />
      ))}
    </ul>
  );
};

export default DesktopMenu;
