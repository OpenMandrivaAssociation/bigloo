%define inplace `pwd`/inplace
%define __noautoprov 'devel.*'
%define __noautoreq 'devel.*'

%define major %{version}
%define devname %mklibname bigloo -d

Summary:	Compiler for the Scheme programming language
Name:		bigloo
Version:	3.8c
Release:	3
License:	GPLv2+
Group:		Development/C
Url:		https://www-sop.inria.fr/mimosa/fp/Bigloo
Source0:	ftp://ftp-sop.inria.fr/mimosa/fp/Bigloo/%{name}%{version}.tar.gz
Source10:	%{name}.rpmlintrc
BuildRequires:	indent
BuildRequires:	pkgconfig(openssl)
BuildRequires:	pkgconfig(sqlite3)
Requires:	indent

%description
Bigloo is a Scheme implementation devoted to one goal: enabling Scheme based
programming style where C(++) is usually required. Bigloo attempts to make
Scheme practical by offering features usually presented by traditional
programming languages but ot offered by Scheme and functional programming.
Bigloo compiles Scheme modules. It delivers small and fast stand alone binary
executables. Bigloo enables full connections between Scheme and C programs.

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

#----------------------------------------------------------------------------

%package -n	%{devname}
Summary:	Static library and header files for the Bigloo library
Group:		Development/C
Provides:	%{name}-devel = %{EVRD}
Requires:	%{name} = %{EVRD}
Requires:	pkgconfig(openssl)
Requires:	pkgconfig(sqlite3)

%description -n	%{devname}
Runtime libraries for Bigloo compiled programs.

This package contains the static Bigloo library and its header files.

%files -n %{devname}
%doc Makefile.config examples
%{_libdir}/bigloo/%{major}/*.a
%{_libdir}/bigloo/%{major}/*.h
%{_libdir}/bigloo/%{major}/Makefile*

#----------------------------------------------------------------------------

%package	doc
Summary:	Bigloo documentation
Group:		Development/C

%description	doc
Documentation for the Bigloo compiler and integrated development environment.

%files doc
%doc manuals/*.html

#----------------------------------------------------------------------------

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

