import type * as React from "react";
import Image from "next/image";
import Link from "next/link";
import {
  Sidebar,
  SidebarContent,
  SidebarHeader,
  SidebarRail,
} from "@/components/ui/sidebar";
import { ThreadList } from "@/components/assistant-ui/thread-list";

export function ThreadListSidebar({
  ...props
}: React.ComponentProps<typeof Sidebar>) {
  return (
    <Sidebar {...props}>
      <SidebarHeader className="aui-sidebar-header mb-2 border-b px-4 py-5">
        <Link href="/" className="transition-opacity hover:opacity-75">
          <Image
            src="/logo-san-2.png"
            alt="SAN AI"
            width={160}
            height={100}
            priority
            className="object-contain"
          />
        </Link>
      </SidebarHeader>
      <SidebarContent className="aui-sidebar-content px-2">
        <ThreadList />
      </SidebarContent>
      <SidebarRail />
    </Sidebar>
  );
}
