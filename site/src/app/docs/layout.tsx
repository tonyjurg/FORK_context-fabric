import { Header } from "@/components/layout";
import { Sidebar, ScrollToTop } from "@/components/docs";
import { fullNavigation } from "@/lib/docs";

export default function DocsLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <>
      <Header />
      <ScrollToTop />
      <div className="flex min-h-screen pt-16">
        <Sidebar navigation={fullNavigation} />
        <main className="flex-1 p-4 md:p-8 overflow-auto bg-[var(--color-bg)] w-full">
          <div className="max-w-4xl mx-auto lg:mx-0">{children}</div>
        </main>
      </div>
    </>
  );
}
