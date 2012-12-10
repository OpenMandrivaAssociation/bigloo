%define inplace `pwd`/inplace
%define _noautoprov ^devel
%define _noautoreq ^devel

%define major %{version}
%define develname %mklibname bigloo -d

Summary:	Compiler for the Scheme programming language
Name:		bigloo
Version:	3.8c
Release:	1
Group:		Development/C
License:	GPLv2+
URL:		http://www-sop.inria.fr/mimosa/fp/Bigloo
Source:		ftp://ftp-sop.inria.fr/mimosa/fp/Bigloo/%{name}%{version}.tar.gz
BuildRequires:	indent
BuildRequires:	sqlite3-devel
BuildRequires:	openssl-devel
Requires:	indent
Obsoletes:	%{_lib}bigloo3.0

%description
Bigloo is a Scheme implementation devoted to one goal: enabling Scheme based
programming style where C(++) is usually required. Bigloo attempts to make
Scheme practical by offering features usually presented by traditional
programming languages but ot offered by Scheme and functional programming.
Bigloo compiles Scheme modules. It delivers small and fast stand alone binary
executables. Bigloo enables full connections between Scheme and C programs.

%package -n	%{develname}
Summary:	Static library and header files for the Bigloo library
Group:		Development/C
Provides:	%{name}-devel = %{version}-%{release}
Requires:	%{name} = %{version}
Requires:	sqlite3-devel
Requires:	openssl-devel

%description -n	%{develname}
Runtime libraries for Bigloo compiled programs.

This package contains the static Bigloo library and its header files.

%package	doc
Summary:	Bigloo documentation
Group:		Development/C

%description	doc
Documentation for the Bigloo compiler and integrated development environment.

%prep
%setup -q -n %{name}%{version}

perl -pi -e "s|bmask=755|bmask=644|" configure

# this is needed to construct a correct soname (fugly)
perl -pi -e "s|^release=.*|release=%{major}|" configure

# fix attributes
find . -type f -perm 0640 -exec chmod 644 {} \;
find . -type d -exec chmod 755 {} \;

%build
export CFLAGS="`echo %{optflags}|sed -e 's/-fomit-frame-pointer//'` -fPIC"
%setup_compile_flags
./configure \
%ifarch x86_64 amd64 athlon
    --arch=athlon \
%endif
%ifarch i586
    --arch=i586 \
%endif
%ifarch i686
    --arch=i686 \
%endif
%ifarch pentium3
    --arch=pentium3 \
%endif
%ifarch pentium4
    --arch=pentium4 \
%endif
    --prefix=%{_prefix} \
    --bindir=%{_bindir} \
    --libdir=%{_libdir} \
    --mandir=%{_mandir}/man1 \
    --infodir=%{_infodir} \
    --docdir=%{_docdir} \
    --bee=full \
    --native-default-backend \
    --emacs=/bin/true \
    --jvm=no \
    --sharedbde=yes \
    --sharedcompiler=yes \
    --coflags="$CFLAGS"

# this is needed to provide a meanful debug package
perl -pi -e "s|STRIP=.*|STRIP=/bin/true|" Makefile.config

# this is needed to construct a correct soname (fugly)
perl -pi -e "s|LDSONAME=.*|LDSONAME=-Wl,-soname|" Makefile.config

# gcc: -pg and -fomit-frame-pointer are incompatible
perl -pi -e "s|-pg||" Makefile.config

export LD_LIBRARY_PATH=`pwd`/lib/%{major}
export BIGLOOLIB=%{inplace}%{_libdir}/bigloo/%{major}
make
make DESTDIR=%{inplace} install

export PATH=`pwd`/bin:$PATH
make compile-bee

# Disable tests as they fail with /usr/bin/bigloo: Command not found
#check
#make test

%install
rm -rf %{buildroot}

export LD_LIBRARY_PATH=`pwd`/lib/%{major}
export BIGLOOLIB=%{inplace}%{_libdir}/bigloo/%{major}

make DESTDIR=%{buildroot} install
make DESTDIR=%{buildroot} install-bee
make -C manuals DESTDIR=%{buildroot} install-bee

chmod 755 %{buildroot}%{_bindir}/*
(
    cd %{buildroot}%{_libdir}
    chmod 755 bigloo/%{major}/*.so
    rm -f *.so
    mv bigloo/%{major}/*.so .

    for ext in bdl calendar fth mail multimedia pth sqlite ssl web
    do
        ln -sf libbigloo${ext}_s-%{major}.so libbigloo${ext}_u-%{major}.so
    done

    (cd bigloo/%{major}; ln -sf ../../*.so .)
)
rm -fr %{buildroot}%{_infodir}/dir
rm -fr %{buildroot}%{_datadir}/doc

perl -pi -e 's|^BOOTBINDIR=.*|BOOTBINDIR=%{_bindir}|' Makefile.config

%files
%{_bindir}/*
%dir %{_libdir}/bigloo/%{major}
%dir %{_libdir}/bigloo/%{major}/bmem
%{_libdir}/bigloo/%{major}/*.init
%{_libdir}/bigloo/%{major}/*.heap
%{_libdir}/bigloo/%{major}/bmem/*
%{_libdir}/bigloo/%{major}/bigloo_config.sch
%{_libdir}/bigloo/%{major}/runtest
%{_libdir}/bigloo/%{major}/text
%{_infodir}/*.info*
%{_mandir}/man*/*
%{_libdir}/lib*.so
%{_libdir}/bigloo/%{major}/*.so

%files -n %{develname}
%doc Makefile.config examples
%{_libdir}/bigloo/%{major}/*.a
%{_libdir}/bigloo/%{major}/*.h
%{_libdir}/bigloo/%{major}/Makefile*

%files doc
%doc manuals/*.html



%changelog
* Fri Jun 15 2012 Andrey Bondrov <abondrov@mandriva.org> 3.8c-1
+ Revision: 805755
- Update to 3.8c
- Drop some legacy junk
- Drop some legacy junk

  + Oden Eriksson <oeriksson@mandriva.com>
    - rebuild

* Thu Sep 10 2009 Thierry Vignaud <tv@mandriva.org> 3.1b-5mdv2010.1
+ Revision: 436809
- rebuild

* Thu Dec 11 2008 Funda Wang <fwang@mandriva.org> 3.1b-4mdv2009.1
+ Revision: 312652
- fix requires

* Wed Dec 10 2008 Funda Wang <fwang@mandriva.org> 3.1b-2mdv2009.1
+ Revision: 312422
- merge lib package into main package
  as the libmajor always be the same as version

* Tue Dec 09 2008 Funda Wang <fwang@mandriva.org> 3.1b-1mdv2009.1
+ Revision: 312153
- New version 3.1b

* Mon Jun 09 2008 Pixel <pixel@mandriva.com> 3.0c-0.2mdv2009.0
+ Revision: 217183
- do not call ldconfig in %%post/%%postun, it is now handled by filetriggers

  + Thierry Vignaud <tv@mandriva.org>
    - fix "foobar is blabla" summary (=> "blabla") so that it looks nice in rpmdrake

* Mon Jan 21 2008 Oden Eriksson <oeriksson@mandriva.com> 3.0c-0.2mdv2008.1
+ Revision: 155496
- make it compile on x86_32
- added some optimizations
- bump release
- fix build
- import bigloo


* Sun Jan 20 2008 Oden Eriksson <oeriksson@mandriva.com> 3.0c-0.1mdv2008.1
- initial Mandriva package
