import { PrismaAdapter } from "@next-auth/prisma-adapter";
import type { NextAuthOptions } from "next-auth";
import NextAuth from "next-auth";
import CredentialsProvider from "next-auth/providers/credentials";
import FacebookProvider from "next-auth/providers/facebook";
import GoogleProvider from "next-auth/providers/google";

import { prisma } from "@/lib/prisma";

const adminEmail = process.env.ADMIN_EMAIL?.toLowerCase();
const ADMIN_USERNAME = "admin";
const ADMIN_PASSWORD = "admin";

export const authOptions: NextAuthOptions = {
  adapter: PrismaAdapter(prisma),
  session: {
    strategy: "jwt",
  },
  jwt: {
    secret: process.env.NEXTAUTH_SECRET,
  },
  providers: [
    CredentialsProvider({
      name: "Local Admin",
      credentials: {
        username: { label: "Username", type: "text" },
        password: { label: "Password", type: "password" },
      },
      async authorize(credentials) {
        if (
          credentials?.username === ADMIN_USERNAME &&
          credentials?.password === ADMIN_PASSWORD
        ) {
          return {
            id: "admin-local",
            name: "Admin",
            email: adminEmail || "admin@localhost",
            role: "ADMIN",
          };
        }
        return null;
      },
    }),
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID ?? "",
      clientSecret: process.env.GOOGLE_CLIENT_SECRET ?? "",
    }),
    FacebookProvider({
      clientId: process.env.FACEBOOK_CLIENT_ID ?? "",
      clientSecret: process.env.FACEBOOK_CLIENT_SECRET ?? "",
    }),
  ],
  events: {
    async createUser({ user }) {
      if (!user.email) {
        return;
      }

      const role = user.email.toLowerCase() === adminEmail ? "ADMIN" : "USER";
      await prisma.user.update({
        where: { id: user.id },
        data: { role },
      });
    },
    async signIn({ user }) {
      if (!user.email) {
        return;
      }

      const role = user.email.toLowerCase() === adminEmail ? "ADMIN" : "USER";
      await prisma.user.update({
        where: { id: user.id },
        data: { role },
      });
    },
  },
  callbacks: {
    async signIn({ user }) {
      return Boolean(user.email);
    },
    async jwt({ token, user }) {
      if (user) {
        token.role = user.role || (user.email?.toLowerCase() === adminEmail ? "ADMIN" : "USER");
        token.id = user.id;
      }
      return token;
    },
    async session({ session, token }) {
      if (session.user) {
        session.user.id = token.id as string;
        session.user.role = token.role as string;
      }
      return session;
    },
  },
  pages: {
    signIn: "/",
  },
};

export default NextAuth(authOptions);
