"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import type { NavItem, NavSection } from "@/types/docs";
import { clsx } from "clsx";
import { useState, useEffect, useCallback } from "react";

function ChevronIcon({ isOpen, className }: { isOpen: boolean; className?: string }) {
  return (
    <svg
      className={clsx(
        "w-4 h-4 transition-transform duration-200",
        isOpen && "rotate-90",
        className
      )}
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={2}
        d="M9 5l7 7-7 7"
      />
    </svg>
  );
}

function MenuIcon({ className }: { className?: string }) {
  return (
    <svg
      className={clsx("w-6 h-6", className)}
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={2}
        d="M4 6h16M4 12h16M4 18h16"
      />
    </svg>
  );
}

function CloseIcon({ className }: { className?: string }) {
  return (
    <svg
      className={clsx("w-6 h-6", className)}
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={2}
        d="M6 18L18 6M6 6l12 12"
      />
    </svg>
  );
}

function NavItemComponent({
  item,
  currentPath,
  depth = 0,
  onNavigate,
}: {
  item: NavItem;
  currentPath: string;
  depth?: number;
  onNavigate?: () => void;
}) {
  const isExternal = item.path.startsWith("http");
  const isActive = !isExternal && currentPath === item.path;
  const hasChildren = item.children && item.children.length > 0;
  const isParentOfActive =
    hasChildren &&
    item.children!.some((child) => currentPath.startsWith(child.path));
  const [isOpen, setIsOpen] = useState(isActive || isParentOfActive);

  const linkClasses = clsx(
    "block py-1.5 px-2 rounded text-[0.875rem] transition-colors flex-1",
    isActive
      ? "bg-[var(--color-accent)] text-white font-medium"
      : "text-[var(--color-text-secondary)] hover:text-[var(--color-text)] hover:bg-[var(--color-border)]"
  );

  const linkStyle = { paddingLeft: `${depth * 12 + 8}px` };

  const handleClick = () => {
    if (onNavigate && !isExternal) {
      onNavigate();
    }
  };

  return (
    <li>
      <div className="flex items-center">
        {hasChildren && (
          <button
            onClick={() => setIsOpen(!isOpen)}
            className="mr-1 p-1 hover:bg-[var(--color-border)] rounded"
            aria-label={isOpen ? "Collapse" : "Expand"}
          >
            <ChevronIcon isOpen={isOpen ?? false} className="w-3 h-3" />
          </button>
        )}
        {isExternal ? (
          <a
            href={item.path}
            target="_blank"
            rel="noopener noreferrer"
            className={linkClasses}
            style={linkStyle}
          >
            {item.title}
            <span className="ml-1 text-[0.75rem] opacity-60">↗</span>
          </a>
        ) : (
          <Link
            href={item.path}
            className={linkClasses}
            style={linkStyle}
            onClick={handleClick}
          >
            {item.title}
          </Link>
        )}
      </div>

      {hasChildren && isOpen && (
        <ul className="mt-1">
          {item.children!.map((child) => (
            <NavItemComponent
              key={child.path}
              item={child}
              currentPath={currentPath}
              depth={depth + 1}
              onNavigate={onNavigate}
            />
          ))}
        </ul>
      )}
    </li>
  );
}

function CollapsibleSection({
  section,
  currentPath,
  defaultOpen = true,
  onNavigate,
}: {
  section: NavSection;
  currentPath: string;
  defaultOpen?: boolean;
  onNavigate?: () => void;
}) {
  const hasActiveItem = section.items.some(
    (item) =>
      currentPath === item.path ||
      currentPath.startsWith(item.path + "/") ||
      (item.children?.some((child) => currentPath.startsWith(child.path)))
  );

  const [isOpen, setIsOpen] = useState(defaultOpen || hasActiveItem);

  useEffect(() => {
    if (hasActiveItem) {
      setIsOpen(true);
    }
  }, [hasActiveItem]);

  return (
    <div>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center justify-between w-full group px-2 py-2 rounded hover:bg-[var(--color-border)] transition-colors"
      >
        <h2 className="text-[0.8125rem] font-bold uppercase tracking-wider text-[var(--color-text)] group-hover:text-[var(--color-accent)]">
          {section.title}
        </h2>
        <ChevronIcon
          isOpen={isOpen}
          className="text-[var(--color-text-secondary)] group-hover:text-[var(--color-accent)]"
        />
      </button>

      {isOpen && (
        <ul className="mt-1 space-y-1">
          {section.items.map((item) => (
            <NavItemComponent
              key={item.path}
              item={item}
              currentPath={currentPath}
              onNavigate={onNavigate}
            />
          ))}
        </ul>
      )}
    </div>
  );
}

function SidebarContent({
  navigation,
  currentPath,
  onNavigate
}: {
  navigation: NavSection[];
  currentPath: string;
  onNavigate?: () => void;
}) {
  return (
    <div className="p-4 space-y-4">
      {navigation.map((section, index) => (
        <CollapsibleSection
          key={section.title}
          section={section}
          currentPath={currentPath}
          defaultOpen={index < 3}
          onNavigate={onNavigate}
        />
      ))}
    </div>
  );
}

interface SidebarProps {
  navigation: NavSection[];
}

export function Sidebar({ navigation }: SidebarProps) {
  const pathname = usePathname();
  const [mobileOpen, setMobileOpen] = useState(false);

  // Close on route change
  useEffect(() => {
    setMobileOpen(false);
  }, [pathname]);

  // Close on escape
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === "Escape") setMobileOpen(false);
    };
    document.addEventListener("keydown", handleEscape);
    return () => document.removeEventListener("keydown", handleEscape);
  }, []);

  // Lock body scroll when mobile menu open
  useEffect(() => {
    document.body.style.overflow = mobileOpen ? "hidden" : "";
    return () => { document.body.style.overflow = ""; };
  }, [mobileOpen]);

  const closeMobile = useCallback(() => setMobileOpen(false), []);

  return (
    <>
      {/* Mobile: FAB to open menu */}
      <button
        onClick={() => setMobileOpen(true)}
        className="lg:hidden fixed bottom-4 right-4 z-40 p-3 bg-[var(--color-accent)] text-white rounded-full shadow-lg hover:opacity-90 transition-opacity"
        aria-label="Open navigation"
      >
        <MenuIcon />
      </button>

      {/* Mobile: Overlay */}
      {mobileOpen && (
        <div
          className="lg:hidden fixed inset-0 bg-black/50 z-40"
          onClick={closeMobile}
        />
      )}

      {/* Mobile: Slide-out drawer */}
      <div
        className={clsx(
          "lg:hidden fixed inset-y-0 left-0 z-50 w-72 bg-[var(--color-bg-alt)] border-r border-[var(--color-border)] transform transition-transform duration-300 ease-in-out",
          mobileOpen ? "translate-x-0" : "-translate-x-full"
        )}
      >
        <div className="flex items-center justify-between p-4 border-b border-[var(--color-border)]">
          <span className="font-semibold text-[var(--color-text)]">Documentation</span>
          <button
            onClick={closeMobile}
            className="p-2 hover:bg-[var(--color-border)] rounded"
            aria-label="Close navigation"
          >
            <CloseIcon className="w-5 h-5" />
          </button>
        </div>
        <div className="overflow-y-auto h-[calc(100%-60px)]">
          <SidebarContent
            navigation={navigation}
            currentPath={pathname}
            onNavigate={closeMobile}
          />
        </div>
      </div>

      {/* Desktop: Static sidebar */}
      <nav className="hidden lg:block w-64 flex-shrink-0 border-r border-[var(--color-border)] bg-[var(--color-bg-alt)] h-[calc(100vh-4rem)] sticky top-16 overflow-y-auto">
        <SidebarContent navigation={navigation} currentPath={pathname} />
      </nav>
    </>
  );
}
