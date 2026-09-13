import type { AppProps } from "next/app";
import "../src/styles/globals.css";
import Layout from "../src/components/Layout";
import { AuthProvider } from "../src/context/AuthContext";
import { CartProvider } from "../src/context/CartContext";

export default function MyApp({ Component, pageProps }: AppProps) {
  return (
    <AuthProvider>
      <CartProvider>
        <Layout>
          <Component {...pageProps} />
        </Layout>
      </CartProvider>
    </AuthProvider>
  );
}
