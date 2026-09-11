import type { AppProps } from "next/app";
import "../src/styles/globals.css";
import Layout from "../src/components/Layout";

export default function MyApp({ Component, pageProps }: AppProps) {
  return (
    <Layout>
      <Component {...pageProps} />
    </Layout>
  );
}