def _set_tampilan() -> None:
    """Tab Pengaturan > Tampilan: wallpaper & warna pilihan User.

    Pratinjau diperbarui LANGSUNG saat pilihan diubah (tanpa menekan
    Simpan) karena widget-nya dibaca dari nilai balik, bukan dari
    settings. Yang tersimpan permanen tetap lewat tombol Simpan.
    """
    s = get_settings()

    st.markdown('<div class="set-section">Warna</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        palet = st.selectbox(
            "Tema warna", PALET_NAMES,
            index=_opt_index(PALET_NAMES, s.get("ui_palet", DEFAULT_PALET)),
            key="set_ui_palet",
            help="Mengubah warna latar, kartu, sidebar, dan teks di seluruh aplikasi.",
        )
    with c2:
        sudut = st.selectbox(
            "Kelengkungan sudut", SUDUT_NAMES,
            index=_opt_index(SUDUT_NAMES, s.get("ui_sudut", "Sedang")),
            key="set_ui_sudut",
            help="Seberapa bulat sudut kartu, gelembung pesan, dan tombol.",
        )

    pakai_aksen = st.checkbox(
        "Pakai warna aksen sendiri", value=bool(s.get("ui_accent_custom")),
        key="set_ui_aksen_on",
        help="Warna tombol utama, tautan, dan tab aktif.",
    )
    if pakai_aksen:
        aksen = st.color_picker(
            "Warna aksen",
            value=(s.get("ui_accent_custom") or palet_aktif(s)["accent"]),
            key="set_ui_aksen",
        )
    else:
        aksen = ""

    st.markdown('<div class="set-section">Wallpaper</div>', unsafe_allow_html=True)
    wp = st.selectbox(
        "Pola latar belakang", WALLPAPER_NAMES,
        index=_opt_index(WALLPAPER_NAMES, s.get("ui_wallpaper", "Polos")),
        key="set_ui_wp",
        help="Pola dibuat dari CSS, jadi ringan dan tidak menambah waktu muat.",
    )

    berkas = st.file_uploader(
        "Atau unggah gambar sendiri (JPG/PNG)",
        type=["jpg", "jpeg", "png", "webp"], key="set_ui_wp_file",
        help="Gambar unggahan menimpa pilihan pola di atas. "
             "Otomatis dikecilkan maks 1920px agar aplikasi tetap ringan.",
    )

    wp_custom = s.get("ui_wallpaper_custom") or ""
    if berkas is not None:
        try:
            wp_custom = siapkan_wallpaper_unggahan(berkas.getvalue())
        except Exception:
            st.warning("Gambar tidak bisa dibaca. Coba berkas lain.")

    if wp_custom:
        k1, k2 = st.columns([3, 1])
        with k1:
            st.caption("Gambar wallpaper sedang dipakai.")
        with k2:
            if st.button("Hapus gambar", key="set_ui_wp_hapus",
                         use_container_width=True):
                _save_settings({"ui_wallpaper_custom": ""}, "Wallpaper gambar dihapus.")
                st.rerun()

    c3, c4 = st.columns(2)
    with c3:
        opac = st.slider(
            "Kepekatan wallpaper", 0, 100,
            value=int(s.get("ui_wallpaper_opacity", 100)), step=5,
            key="set_ui_wp_opac",
            help="Turunkan kalau wallpaper membuat teks susah dibaca.",
        )
    with c4:
        blur = st.slider(
            "Buram", 0, 20, value=int(s.get("ui_wallpaper_blur", 0)),
            key="set_ui_wp_blur",
            help="Berguna untuk foto unggahan supaya teks tetap jelas terbaca.",
        )

    # Pratinjau memakai pilihan SAAT INI, bukan yang tersimpan.
    pratinjau = dict(s)
    pratinjau.update({
        "ui_palet": palet, "ui_sudut": sudut,
        "ui_accent_custom": aksen if (pakai_aksen and _valid_hex(aksen)) else "",
        "ui_wallpaper": wp, "ui_wallpaper_custom": wp_custom,
        "ui_wallpaper_opacity": opac, "ui_wallpaper_blur": blur,
    })
    st.markdown('<div class="set-section">Pratinjau</div>', unsafe_allow_html=True)
    st.markdown(kartu_pratinjau(pratinjau), unsafe_allow_html=True)
    st.caption("Tekan Simpan untuk menerapkan ke seluruh aplikasi.")

    def _reset() -> None:
        _save_settings({
            "ui_palet": DEFAULT_PALET, "ui_sudut": "Sedang",
            "ui_accent_custom": "", "ui_wallpaper": "Polos",
            "ui_wallpaper_custom": "", "ui_wallpaper_opacity": 100,
            "ui_wallpaper_blur": 0,
        }, "Tampilan dikembalikan ke bawaan.")
        st.rerun()

    _baris_aksi_simpan(
        "Simpan perubahan", "save_tampilan",
        {
            "ui_palet": palet, "ui_sudut": sudut,
            "ui_accent_custom": aksen if (pakai_aksen and _valid_hex(aksen)) else "",
            "ui_wallpaper": wp, "ui_wallpaper_custom": wp_custom,
            "ui_wallpaper_opacity": opac, "ui_wallpaper_blur": blur,
        },
        "Tampilan disimpan.",
        sekunder=("Kembalikan ke bawaan", "reset_tampilan", _reset),
    )


