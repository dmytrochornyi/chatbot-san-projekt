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
      <SidebarHeader className="aui-sidebar-header mb-2 border-b px-4 py-3">
        <Link href="/" className="flex items-center transition-opacity hover:opacity-75">
          <Image
            src="/logo-san-2.png"
            alt="SAN AI"
            width={1255}
            height={365}
            priority
            className="w-40 h-auto object-contain"
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
